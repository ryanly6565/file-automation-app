
from src.rules import Rule
from pathlib import Path
from src.actions import (
    MoveAction,
    CopyAction,
    ExecuteScriptAction,
    DeleteAction
)


def get_rule_warnings(rule: Rule) -> list[str]:
    warning_list = []
    copy_warning_added = False
    script_warning_added = False
    script_followup_warning_added = False
    watch_folder = rule.watch_folder.resolve()

    for index, action in enumerate(rule.actions):
        if isinstance(action, (MoveAction, CopyAction)):
            destination = action.dst_directory.resolve()

            if destination == watch_folder:
                warning_list.append(
                    "This destination is the watched folder. "
                    "This may cause repeated rule processing."
                )

            elif rule.recursive and watch_folder in destination.parents:
                warning_list.append(
                    "This destination is inside the recursively watched folder. "
                    "This may cause repeated rule processing."
                )

        if isinstance(action, CopyAction) and index < len(rule.actions) - 1 and not copy_warning_added:
            warning_list.append("After a copy, additional actions will operate on the original file.")
            copy_warning_added = True

        if isinstance(action, ExecuteScriptAction) and not script_warning_added:
            warning_list.append(
                "This rule runs an external script. "
                "The script may modify, create, move, or delete files in ways the app cannot predict."
            )
            script_warning_added = True

        if (isinstance(action, ExecuteScriptAction) and index < len(rule.actions) - 1 and not script_followup_warning_added):
            warning_list.append(
                "This rule has actions after a script. "
                "Those actions will continue using the current file path, even if the script changed the file externally."
            )
            script_followup_warning_added = True

    return warning_list

def validate_rule(rule: Rule) -> None:
    """Raises ValueError if the rule contains invalid folders/files"""
    rule_name = rule.name

    if not rule.watch_folder.exists():
        raise ValueError(f"In the rule '{rule_name}': Watch folder does not exist")
    if not rule.watch_folder.is_dir():
        raise ValueError(f"In the rule '{rule_name}': Watch folder is not a directory")

    for action in rule.actions:
        if isinstance(action, MoveAction) or isinstance(action, CopyAction):
            if not action.dst_directory.exists():
                raise ValueError(f"In the rule '{rule_name}': Destination folder does not exist")
            if not action.dst_directory.is_dir():
                raise ValueError(f"In the rule '{rule_name}': Destination folder is not a directory")
        if isinstance(action, ExecuteScriptAction):
            if not action.script.exists():
                raise ValueError(f"In the rule '{rule_name}': Script does not exist")
            if not action.script.is_file():
                raise ValueError(f"In the rule '{rule_name}': Script path is not a file:\n{action.script}")

    # delete CANNOT be an action that is not in the last position
    for index, action in enumerate(rule.actions):
        if isinstance(action, DeleteAction) and index != len(rule.actions) - 1:
            raise ValueError("Delete action must be the final action in a rule.")