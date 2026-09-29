from src.rules import Rule
from src.conditions import *
from src.actions import *

def test_matching_file_gets_action(tmp_path):
    """Verify action is applied on successful match."""
    source_dir = tmp_path / "source"
    destination_dir = tmp_path / "destination"

    source_dir.mkdir()
    destination_dir.mkdir()

    file = source_dir / "example.txt"
    file.write_text("hello")

    rule = Rule(ExtensionCondition(".txt"), [MoveAction(destination_dir)], source_dir, "Rule 1")
    if rule.matches(file):
        rule.execute(file)

    assert not file.exists()
    assert (destination_dir / "example.txt").exists()

def test_non_matching_file_gets_no_action(tmp_path):
    """Verify action is not applied on unsuccessful match."""
    source_dir = tmp_path / "source"
    destination_dir = tmp_path / "destination"

    source_dir.mkdir()
    destination_dir.mkdir()

    file = source_dir / "example.md"
    file.write_text("hello")

    rule = Rule(ExtensionCondition(".txt"), [MoveAction(destination_dir)], source_dir, "Rule 1")
    if rule.matches(file):
        rule.execute(file)

    assert file.exists()
    assert not (destination_dir / "example.md").exists()

def test_chain_of_actions_same_file(tmp_path):
    """Verify a sequence of actions is applied succesfully, where there is only ever 1 file."""
    source_dir = tmp_path / "source"
    destination_dir = tmp_path / "destination"

    source_dir.mkdir()
    destination_dir.mkdir()

    file = source_dir / "example.txt"
    file.write_text("hello")

    rule = Rule(ExtensionCondition(".txt"), [MoveAction(destination_dir), PrefixRenamingAction("new_")], source_dir, "Rule 1")
    if rule.matches(file):
        rule.execute(file)

    assert not file.exists()
    assert not (destination_dir / "example.txt").exists()
    assert (destination_dir / "new_example.txt").exists()

def test_chain_of_actions_same_file_alt_order(tmp_path):
    """Verify athe same sequence of actions is applied succesfully, but in the reverse order."""
    source_dir = tmp_path / "source"
    destination_dir = tmp_path / "destination"

    source_dir.mkdir()
    destination_dir.mkdir()

    file = source_dir / "example.txt"
    file.write_text("hello")

    rule = Rule(ExtensionCondition(".txt"), [PrefixRenamingAction("new_"), MoveAction(destination_dir)], source_dir, "Rule 1")
    if rule.matches(file):
        rule.execute(file)

    assert not file.exists()
    assert not (destination_dir / "example.txt").exists()
    assert (destination_dir / "new_example.txt").exists()

def test_disabled_rule_does_not_match(tmp_path):
    """Test that a file that should pass a rule fails if it is disabled"""
    file = tmp_path / "test.txt"
    file.write_text("hello")
    rule = Rule(condition=ExtensionCondition(".txt"), actions=[], watch_folder=tmp_path, name="Test Rule", enabled=False,)
    assert not rule.matches(file)

def test_enabled_rule_does_match(tmp_path):
    """Test that the very same rule/file that failed above passes when it is enabled """
    file = tmp_path / "test.txt"
    file.write_text("hello")
    rule = Rule(condition=ExtensionCondition(".txt"), actions=[], watch_folder=tmp_path, name="Test Rule", enabled=True,)
    assert rule.matches(file)