import pytest

from src.rule_validation import validate_rule, get_rule_warnings
from src.rules import Rule
from src.conditions import ExtensionCondition
from src.actions import MoveAction, CopyAction, ExecuteScriptAction, DeleteAction

def test_validate_rule_accepts_valid_folders(tmp_path):
    """Verify that passable folders are accepted """
    watch = tmp_path / "watch"
    destination = tmp_path / "destination"

    watch.mkdir()
    destination.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(destination)],
        watch_folder=watch,
        name="Test",
    )

    # expect no exception raised
    validate_rule(rule)

def test_validate_rejects_missing_watch_folder(tmp_path):
    """Verify that missing watch folders are not accepted """
    watch = tmp_path / "watch"
    destination = tmp_path / "destination"

    watch.mkdir()
    destination.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(destination)],
        watch_folder=tmp_path / "missing",
        name="Test",
    )

    with pytest.raises(ValueError):
        validate_rule(rule)

def test_validate_rejects_missing_destination(tmp_path):
    """Verify that missing destination folders are not accepted """
    watch = tmp_path / "watch"
    destination = tmp_path / "missing"

    watch.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(destination)],
        watch_folder=watch,
        name="Test",
    )

    with pytest.raises(ValueError):
        validate_rule(rule)

def test_get_rule_warnings_warns_when_watch_is_destination(tmp_path):
    """Verify that the proper warning is given when watch is destination """
    watch = tmp_path / "watch"
    watch.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(watch)],
        watch_folder=watch,
        name="Test",
    )

    warnings = get_rule_warnings(rule)
    assert any(
        "destination is the watched folder" in warning
        for warning in warnings
    )


def test_get_rule_warnings_warns_when_watch_is_parent_of_destination(tmp_path):
    """Verify that the proper warning is given when watch is parent of destination """
    watch = tmp_path / "watch"
    destination = watch / "dst"

    watch.mkdir()
    destination.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[CopyAction(destination)],
        watch_folder=watch,
        name="Test",
        recursive=True
    )

    warnings = get_rule_warnings(rule)
    assert any(
        "inside the recursively watched folder" in warning
        for warning in warnings
    )

def test_no_recursive_subfolder_warning_when_not_recursive(tmp_path):
    """Verify that no warning is given when watch is destination """
    watch = tmp_path / "watch"
    destination = watch / "dst"

    watch.mkdir()
    destination.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(destination)],
        watch_folder=watch,
        name="Test",
        recursive=False,
    )

    warnings = get_rule_warnings(rule)

    assert not any(
        "inside the recursively watched folder" in warning
        for warning in warnings
    )

def test_get_rule_warnings_warn_for_execute_script(tmp_path):
    """Verify that no warning is given when watch is destination """
    watch = tmp_path / "watch"
    destination = watch / "dst"
    script = watch / "script.py"

    watch.mkdir()
    destination.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[ExecuteScriptAction(script), MoveAction(destination)],
        watch_folder=watch,
        name="Test",
        recursive=False,
    )

    warnings = get_rule_warnings(rule)

    assert any(
        "rule runs an external script" in warning
        for warning in warnings
    )
    assert any(
        "rule has actions after a script" in warning
        for warning in warnings
    )


def test_delete_can_not_be_non_last(tmp_path):
    """Verify that a delete action cannot be a non-terminal action"""
    watch = tmp_path / "watch"
    destination = watch / "dst"
    script = watch / "script.py"

    watch.mkdir()
    destination.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[DeleteAction(False), MoveAction(destination)],
        watch_folder=watch,
        name="Test",
        recursive=False,
    )

    with pytest.raises(ValueError):
        validate_rule(rule)


def test_delete_can_be_last(tmp_path):
    """Verify that a delete action can be the last action"""
    watch = tmp_path / "watch"
    destination = watch / "dst"
    script = watch / "script.py"

    watch.mkdir()
    destination.mkdir()

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(destination), DeleteAction(False),],
        watch_folder=watch,
        name="Test",
        recursive=False,
    )

    validate_rule(rule)














