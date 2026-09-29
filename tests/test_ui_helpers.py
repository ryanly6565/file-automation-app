from src.ui import (
    move_rule_helper,
    group_rules_by_folder,
    find_matching_rule,
)
from src.rules import Rule
from src.conditions import ExtensionCondition

class TestMoveRule:
    def test_move_rule_up(self, tmp_path):
        """Verify that move rule can successfully move a rule up."""
        folder = tmp_path / "incoming"

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="A",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="B",
        )

        rules = [rule_a, rule_b]
        move_rule_helper(rules, rule_b, -1)
        assert rules == [rule_b, rule_a]

    def test_move_rule_down(self, tmp_path):
        """Verify that move rule can successfully move a rule down."""
        folder = tmp_path / "incoming"

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="A",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="B",
        )

        rules = [rule_a, rule_b]
        move_rule_helper(rules, rule_a, 1)
        assert rules == [rule_b, rule_a]

    def test_move_rule_up_does_nothing_on_first(self, tmp_path):
        """Verify that move rule cannot move a rule up if its first."""
        folder = tmp_path / "incoming"

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="A",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="B",
        )

        rules = [rule_a, rule_b]
        move_rule_helper(rules, rule_a, -1)
        assert rules == [rule_a, rule_b]

    def test_move_rule_down_does_nothing_on_last(self, tmp_path):
        """Verify that move rule cannot move a rule down if its last."""
        folder = tmp_path / "incoming"

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="A",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="B",
        )

        rules = [rule_a, rule_b]
        move_rule_helper(rules, rule_b, 1)
        assert rules == [rule_a, rule_b]

    def test_move_rule_does_not_cross_folders(self, tmp_path):
        """Verify that move rule will ignore rules from other folders when moving a rule."""
        folder_a = tmp_path / "a"
        folder_b = tmp_path / "b"

        rule_a1 = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_a,
            name="A1",
        )

        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_b,
            name="B",
        )

        rule_a2 = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_a,
            name="A2",
        )

        rules = [rule_a1, rule_b, rule_a2]
        move_rule_helper(rules, rule_a2, -1)
        assert rules == [rule_a2, rule_b, rule_a1]


class TestGroupRulesByFolder:
    def test_groups_rules_with_same_folder(self, tmp_path):
        """Verify that group rules works with two rules of the same folder."""
        folder = tmp_path / "incoming"

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="A",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".md"),
            actions=[],
            watch_folder=folder,
            name="B",
        )

        grouped = group_rules_by_folder([rule_a, rule_b])
        assert list(grouped.keys()) == [folder]
        assert grouped[folder] == [rule_a, rule_b]

    def test_separates_rules_with_different_folders(self, tmp_path):
        """Verify that group rules works with two rules of different folders."""
        folder_a = tmp_path / "a"
        folder_b = tmp_path / "b"

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_a,
            name="A",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_b,
            name="B",
        )

        grouped = group_rules_by_folder([rule_a, rule_b])
        assert grouped[folder_a] == [rule_a]
        assert grouped[folder_b] == [rule_b]

    def test_preserves_rule_order_within_folder(self, tmp_path):
        """Verify that the order of rules in the dict are the same as before they were grouped."""
        folder = tmp_path / "incoming"

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="A",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".md"),
            actions=[],
            watch_folder=folder,
            name="B",
        )
        rule_c = Rule(
            condition=ExtensionCondition(".py"),
            actions=[],
            watch_folder=folder,
            name="C",
        )

        grouped = group_rules_by_folder([rule_a, rule_b, rule_c])
        assert grouped[folder] == [rule_a, rule_b, rule_c]

    def test_empty_rules_returns_empty_group(self):
        """Verify that calling group rules on an empty liust returns and empty dict."""
        grouped = group_rules_by_folder([])
        assert len(grouped) == 0

class TestFindMatchingRule:
    def test_find_matching_rule_returns_first_match(self, tmp_path):
        """Verify that find matching rule returns the very first match."""
        folder = tmp_path / "incoming"
        folder.mkdir()
        file = folder / "test.txt"
        file.write_text("hello")

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="1",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder,
            name="2",
        )

        result = find_matching_rule([rule_a, rule_b], file)
        assert result is rule_a

    def test_find_matching_rule_ignores_other_folders(self, tmp_path):
        """Verify that find matching rule ignores non-matching rules but still accepts matching."""
        folder_a = tmp_path / "a"
        folder_b = tmp_path / "b"

        folder_a.mkdir()
        folder_b.mkdir()

        file = folder_a / "test.txt"
        file.write_text("hello")

        rule_a = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_b,
            name="Wrong Folder",
        )
        rule_b = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_a,
            name="Correct Folder",
        )

        result = find_matching_rule([rule_a, rule_b], file)
        assert result == rule_b

    def test_find_matching_rule_returns_none_if_no_matches(self, tmp_path):
        """Verify that find matching rule ignoress non-matching rules."""
        folder_a = tmp_path / "a"
        folder_b = tmp_path / "b"

        folder_a.mkdir()
        folder_b.mkdir()

        file = folder_a / "test.txt"
        file.write_text("hello")

        rule = Rule(
            condition=ExtensionCondition(".txt"),
            actions=[],
            watch_folder=folder_b,
            name="Wrong Folder",
        )

        result = find_matching_rule([rule], file)
        assert result is None




