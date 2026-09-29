import pytest
import json
from src.config_loader import load_rules, make_condition_from_json, make_actions_from_json
from src.conditions import *
from src.actions import *
from src.rules import Rule

class TestConfigLoader:
    def test_valid_config_works_correctly(self, tmp_path):
        """Verify config loader can successfully load a simple config"""
        config = {
            "rules": [
                {
                    "name": "Sort text notes",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                            "type": "prefix_rename",
                            "value": "processed_"
                        }
                    ]
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        rules = load_rules(file)
        assert rules[0].watch_folder == Path("sandbox/incoming")
        assert isinstance(rules, list)
        assert len(rules) == 1

        rule = rules[0]
        assert isinstance(rule.condition, ExtensionCondition)
        assert isinstance(rule.actions, list)
        assert len(rule.actions) == 1
        assert isinstance(rule.actions[0], PrefixRenamingAction)

    def test_config_loader_parses_multiple_rules(self, tmp_path):
        """Verify config loader can successfully load multiple rules"""
        config = {
            "rules": [
                {
                    "name": "Sort text notes",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                            "type": "prefix_rename",
                            "value": "processed_"
                        }
                    ]
                },
                {
                    "name": "Sort pdf notes",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "name_contains",
                        "value": "recipe"
                    },
                    "actions": [
                        {
                            "type": "suffix_rename",
                            "value": "_finished"
                        }
                    ]
                },
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        rules = load_rules(file)
        assert isinstance(rules, list)
        assert len(rules) == 2

        rule_1 = rules[0]
        assert isinstance(rule_1.condition, ExtensionCondition)
        assert isinstance(rule_1.actions, list)
        assert len(rule_1.actions) == 1
        assert isinstance(rule_1.actions[0], PrefixRenamingAction)

        rule_2 = rules[1]
        assert isinstance(rule_2.condition, NameContainsCondition)
        assert isinstance(rule_2.actions, list)
        assert len(rule_2.actions) == 1
        assert isinstance(rule_2.actions[0], SuffixRenamingAction)

    def test_complex_config_works_correctly(self, tmp_path):
        """Verify config loader can successfully load a config with complex rules and actions"""
        config = {
            "watch_folder": "sandbox/incoming",
            "rules": [
                {
                "name": "Sort text notes",
                "watch_folder": "sandbox/incoming",
                "condition": {
                    "type": "and",
                    "conditions": [
                    {
                        "type": "extension",
                        "value": ".txt"
                    },
                    {
                        "type": "name_contains",
                        "value": "notes",
                        "case_sensitive": False
                    }
                    ]
                },
                "actions": [
                    {
                    "type": "prefix_rename",
                    "value": "processed_"
                    },
                    {
                    "type": "move",
                    "destination": "sandbox/sorted"
                    }
                ]
                }
            ]
        }
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        rules = load_rules(file)
        assert isinstance(rules, list)
        assert len(rules) == 1

        rule = rules[0]
        assert isinstance(rule.condition, AndCondition)
        assert isinstance(rule.condition.conditions[0], ExtensionCondition)
        assert isinstance(rule.condition.conditions[1], NameContainsCondition)

        assert isinstance(rule.actions, list)
        assert len(rule.actions) == 2
        assert isinstance(rule.actions[0], PrefixRenamingAction)
        assert isinstance(rule.actions[1], MoveAction)

    def test_config_loader_missing_watch_folder(self, tmp_path):
        """Verify an error is thrown when trying to load a config without a watch folder in a rule"""
        config = {
            "rules": [
                {
                "name": "Sort text notes",
                "condition": {
                    "type": "extension",
                    "value": ".txt"
                },
                "actions": [
                    {
                    "type": "prefix_rename",
                    "value": "processed_"
                    }
                ]
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)

    def test_config_loader_wrongly_typed_watch_folder(self, tmp_path):
        """Verify an error is thrown when trying to load a config with a watch folder that is not a string"""
        config = {
            "rules": [
                {
                "name": "Sort text notes",
                "watch_folder": 1,
                "condition": {
                    "type": "extension",
                    "value": ".txt"
                },
                "actions": [
                    {
                    "type": "prefix_rename",
                    "value": "processed_"
                    }
                ]
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)

    def test_config_loader_empty_watch_folder(self, tmp_path):
        """Verify an error is thrown when trying to load a config with a blank watch folder"""
        config = {
            "rules": [
                {
                "name": "Sort text notes",
                "watch_folder": "",
                "condition": {
                    "type": "extension",
                    "value": ".txt"
                },
                "actions": [
                    {
                    "type": "prefix_rename",
                    "value": "processed_"
                    }
                ]
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)

    def test_config_loader_missing_rules(self, tmp_path):
        """Verify an error is thrown when trying to load a config without rules"""
        config = {
            "watch_folder": "sandbox/incoming",
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)

    def test_config_loader_wrongly_typed_rules(self, tmp_path):
        """Verify an error is thrown when trying to load a config with rules that are not a list"""
        config = {
            "watch_folder": "sandbox/incoming",
            "rules": {
                "name": "Sort text notes",
                "watch_folder": "sandbox/incoming",
                "condition": {
                    "type": "extension",
                    "value": ".txt"
                },
                "actions": [
                    {
                    "type": "prefix_rename",
                    "value": "processed_"
                    }
                ]
            }
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)

    def test_config_loader_empty_rules(self, tmp_path):
        """Verify an error is thrown when trying to load a config with an empty list of rules"""
        config = {
            "rules": []
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        rules = load_rules(file)
        assert rules == []
        
    def test_config_loader_rules_missing_name(self, tmp_path):
        """Verify an error is thrown when trying to load a config with a rule with no name"""
        config = {
            "watch_folder": "sandbox/incoming",
            "rules": [
                    {
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                        "type": "prefix_rename",
                        "value": "processed_"
                        }
                    ]
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)
            
    def test_config_loader_rules_wrongly_typed_name(self, tmp_path):
        """Verify an error is thrown when trying to load a config with a rule with a non string name"""
        config = {
            "watch_folder": "sandbox/incoming",
            "rules": [
                    {
                    "name": 3,
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                        "type": "prefix_rename",
                        "value": "processed_"
                        }
                    ]
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)
            
    def test_config_loader_rules_empty_name(self, tmp_path):
        """Verify an error is thrown when trying to load a config with a rule with an empty name"""
        config = {
            "watch_folder": "sandbox/incoming",
            "rules": [
                    {
                    "name": "",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                        "type": "prefix_rename",
                        "value": "processed_"
                        }
                    ]
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)


    def test_rule_enabled_false_is_loaded(self, tmp_path):
        """Verify config loader can successfully parse a disabled rule"""
        config = {
            "rules": [
                {
                    "name": "Sort text notes",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                            "type": "prefix_rename",
                            "value": "processed_"
                        }
                    ],
                    "enabled": False
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        rules = load_rules(file)
        assert rules[0].enabled == False
        

        
    def test_rule_enabled_default_true(self, tmp_path):
        """Verify config loader defaults enabled to True if not provided"""
        config = {
            "rules": [
                {
                    "name": "Sort text notes",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                            "type": "prefix_rename",
                            "value": "processed_"
                        }
                    ],
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        rules = load_rules(file)
        assert rules[0].enabled == True
  
    def test_config_loader_rules_wrongly_typed_enabled(self, tmp_path):
        """Verify an error is thrown when trying to load a config with a non-bool enabled field"""
        config = {
            "rules": [
                {
                    "name": "Sort text notes",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                            "type": "prefix_rename",
                            "value": "processed_"
                        }
                    ],
                    "enabled": "True",
                }
            ]
        }
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text(json.dumps(config))

        with pytest.raises(ValueError):
            load_rules(file)

    def test_load_move_action_collision_policy(self, tmp_path):
        """Verify a collision policy can be successfully parsed"""
        config = tmp_path / "rules.json"
        config.write_text("""
        {
            "rules": [
                {
                    "name": "Test",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                            "type": "move",
                            "destination": "sandbox/sorted",
                            "collision_policy": "skip"
                        }
                    ]
                }
            ]
        }
        """)

        rules = load_rules(str(config))
        action = rules[0].actions[0]
        assert isinstance(action, MoveAction)
        assert action.collision_policy == "skip"

    def test_missing_collision_policy_defaults_to_rename(self, tmp_path):
        """Verify a missing collision policy defaults to rename"""
        config = tmp_path / "rules.json"
        config.write_text("""
        {
            "rules": [
                {
                    "name": "Test",
                    "watch_folder": "sandbox/incoming",
                    "condition": {
                        "type": "extension",
                        "value": ".txt"
                    },
                    "actions": [
                        {
                            "type": "copy",
                            "destination": "sandbox/sorted"
                        }
                    ]
                }
            ]
        }
        """)

        rules = load_rules(str(config))
        action = rules[0].actions[0]
        assert isinstance(action, CopyAction)
        assert action.collision_policy == "rename"