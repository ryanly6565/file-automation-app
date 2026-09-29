import pytest
import json
from src.config_loader import make_condition_from_json
from src.conditions import *

class TestConditionsConfigLoader:
    def test_missing_condition_type(self):
        """Verify an error is thrown when trying to read a condition missing a type"""
        condition_data = {}

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_wrong_typed_condition_type(self):
        """Verify an error is thrown when trying to read a condition missing a type"""
        condition_data = {
            "type": 30
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestExtensionConditionConfigLoader:
    def test_extension_condition_created(self):
        """Verify an extension condition can successfully be created"""
        condition_data = {
            "type": "extension",
            "value": ".txt"
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, ExtensionCondition)
        assert condition.matches(Path("notes.txt"))

    def test_extension_condition_missing_value(self):
        """Verify an error is thrown when trying to read an extension condition missing a value"""
        condition_data = {
            "type": "extension",
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_extension_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read an extension condition with a wrongly typed value"""
        condition_data = {
            "type": "extension",
            "value": 4
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestNameContainsConditionConfigLoader:
    def test_name_contains_condition_created(self):
        """Verify a name contains condition can successfully be created"""
        condition_data = {
            "type": "name_contains",
            "value": "notes"
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, NameContainsCondition)
        assert condition.matches(Path("notes.txt"))

    def test_name_contains_condition_missing_value(self):
        """Verify an error is thrown when trying to read a name contains condition missing a value"""
        condition_data = {
            "type": "name_contains",
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_contains_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read a name contains condition with a wrongly typed value"""
        condition_data = {
            "type": "name_contains",
            "value": 4
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_contains_condition_wrong_case_sensitive_type(self):
        """Verify a name contains condition can be created with only a bool type case_sensitive value"""
        condition_data = {
            "type": "name_contains",
            "value": "NOTES",
            "case_sensitive": 12
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestNameStartsWithConditionConfigLoader:
    def test_name_starts_with_condition_created(self):
        """Verify a name starts with condition can successfully be created"""
        condition_data = {
            "type": "name_starts_with",
            "value": "notes",
            "case_sensitive": True,
            "include_extension": False
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, NameStartsWithCondition)
        assert condition.matches(Path("notes123.txt"))

    def test_name_starts_with_condition_missing_value(self):
        """Verify an error is thrown when trying to read a name starts with condition missing a value"""
        condition_data = {
            "type": "name_starts_with",
            "case_sensitive": True,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_starts_with_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read a name starts withcondition with a wrongly typed value"""
        condition_data = {
            "type": "name_starts_with",
            "value": 4,
            "case_sensitive": True,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_starts_with_condition_wrong_case_sensitive_type(self):
        """Verify a name starts with condition can be created with only a bool case_sensitive value"""
        condition_data = {
            "type": "name_starts_with",
            "value": "NOTES",
            "case_sensitive": 12,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_starts_with_condition_wrong_include_extension_type(self):
        """Verify a name starts with condition can be created with only a bool case_sensitive value"""
        condition_data = {
            "type": "name_starts_with",
            "value": "NOTES",
            "case_sensitive": True,
            "include_extension": 12,
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestNameEndsWithConditionConfigLoader:
    def test_name_ends_with_condition_created(self):
        """Verify a name ends with condition can successfully be created"""
        condition_data = {
            "type": "name_ends_with",
            "value": "notes",
            "case_sensitive": True,
            "include_extension": False
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, NameEndsWithCondition)
        assert condition.matches(Path("notes.txt"))

    def test_name_ends_with_condition_missing_value(self):
        """Verify an error is thrown when trying to read a name ends with condition missing a value"""
        condition_data = {
            "type": "name_ends_with",
            "case_sensitive": True,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_ends_with_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read a name ends with condition with a wrongly typed value"""
        condition_data = {
            "type": "name_ends_with",
            "value": 4,
            "case_sensitive": True,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_ends_with_condition_wrong_case_sensitive_type(self):
        """Verify a name ends with condition can be created with only a bool case_sensitive value"""
        condition_data = {
            "type": "name_ends_with",
            "value": "NOTES",
            "case_sensitive": 12,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_name_ends_with_condition_wrong_include_extension_type(self):
        """Verify a name ends with condition can be created with only a bool case_sensitive value"""
        condition_data = {
            "type": "name_ends_with",
            "value": "NOTES",
            "case_sensitive": True,
            "include_extension": 12,
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestExactNameConditionConfigLoader:
    def test_exact_name_condition_created(self):
        """Verify an exact name condition can successfully be created"""
        condition_data = {
            "type": "exact_name",
            "value": "notes",
            "case_sensitive": True,
            "include_extension": False
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, ExactNameCondition)
        assert condition.matches(Path("notes.txt"))

    def test_exact_name_with_condition_missing_value(self):
        """Verify an error is thrown when trying to read an exact name condition missing a value"""
        condition_data = {
            "type": "exact_name",
            "case_sensitive": True,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_exact_name_with_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read an exact name condition with a wrongly typed value"""
        condition_data = {
            "type": "exact_name",
            "value": 4,
            "case_sensitive": True,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_exact_name_with_condition_wrong_case_sensitive_type(self):
        """Verify an exact name condition can be created with only a bool case_sensitive value"""
        condition_data = {
            "type": "exact_name",
            "value": "NOTES",
            "case_sensitive": 12,
            "include_extension": False
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_exact_name_with_condition_wrong_include_extension_type(self):
        """Verify an exact name with condition can be created with only a bool case_sensitive value"""
        condition_data = {
            "type": "exact_name",
            "value": "NOTES",
            "case_sensitive": True,
            "include_extension": 12,
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestAndContainsConditionConfigLoader:
    def test_and_condition_created_two_conditions(self):
        """Verify an and condition with two conditions can successfully be created"""
        condition_data = {
            "type": "and",
            "conditions": [
                {
                    "type": "extension",
                    "value": ".txt"
                },
                {
                    "type": "name_contains",
                    "value": "notes",
                }
            ]
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, AndCondition)
        assert condition.matches(Path("notes.txt"))

    def test_and_condition_created_one_conditions(self):
        """Verify an and condition with two conditions can successfully be created"""
        condition_data = {
            "type": "and",
            "conditions": [
                {
                    "type": "extension",
                    "value": ".txt"
                },
            ]
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, AndCondition)
        assert condition.matches(Path("report.txt"))
        assert not condition.matches(Path("report.md"))

    def test_and_condition_created_no_conditions(self):
        """Verify an empty rules list is allowed."""
        condition_data = {
            "type": "and",
            "conditions": []
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_and_condition_missing_value(self):
        """Verify an error is thrown when trying to read an and condition missing conditions"""
        condition_data = {
            "type": "and",
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_and_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read an and condition with a wrongly typed conditions field"""
        condition_data = {
            "type": "and",
            "conditions": 3
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestOrConditionConfigLoader:
    def test_or_condition_created_two_conditions(self):
        """Verify an or condition with two conditions can successfully be created"""
        condition_data = {
            "type": "or",
            "conditions": [
                {
                    "type": "extension",
                    "value": ".txt"
                },
                {
                    "type": "name_contains",
                    "value": "notes",
                }
            ]
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, OrCondition)
        assert condition.matches(Path("notes.md"))

    def test_or_condition_created_one_conditions(self):
        """Verify an or condition with two conditions can successfully be created"""
        condition_data = {
            "type": "or",
            "conditions": [
                {
                    "type": "extension",
                    "value": ".txt"
                },
            ]
        }

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, OrCondition)
        assert condition.matches(Path("report.txt"))
        assert not condition.matches(Path("report.md"))

    def test_or_condition_created_no_conditions(self):
        """Verify an or condition cannot be created with no child conditions."""
        condition_data = {
            "type": "or",
            "conditions": []
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_or_condition_missing_value(self):
        """Verify an error is thrown when trying to read an or condition missing conditions"""
        condition_data = {
            "type": "or",
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_or_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read an or condition with a wrongly typed conditions field"""
        condition_data = {
            "type": "or",
            "conditions": 3
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

class TestSizeConditionConfigLoader:
    def test_size_condition_created(self, tmp_path):
        """Verify an size condition can be successfully created"""
        condition_data = {
            "type": "size",
            "value": 10,
            "comparison": "gt"
        }

        file = tmp_path / "notes.txt"
        file.write_bytes(b"x" * 11)

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, SizeCondition)
        assert condition.matches(file)

        file.write_bytes(b"x" * 10)
        assert not condition.matches(file)

    def test_size_condition_no_size(self):
        """Verify a size condition cannot be created with no value for size."""
        condition_data = {
            "type": "size",
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_size_condition_no_size(self):
        """Verify a size condition cannot be created with a wrongly typed value for size."""
        condition_data = {
            "type": "size",
            "size": "123"
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_size_condition_wrong_value_type(self):
        """Verify an error is thrown when trying to read an and condition with a wrongly typed conditions field"""
        condition_data = {
            "type": "and",
            "conditions": 3
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_size_condition_explicit_greater_than(self, tmp_path):
        """Verify a size condition can be created with a correct typed but explicit greater_than."""
        condition_data = {
            "type": "size",
            "value": 10,
            "comparison": "lt"
        }

        file = tmp_path / "notes.txt"

        condition = make_condition_from_json(condition_data, "test_rule")
        assert isinstance(condition, SizeCondition)

        file.write_bytes(b"x" * 9)
        assert condition.matches(file)

        file.write_bytes(b"x" * 10)
        assert not condition.matches(file)

    def test_size_condition_wrongly_typed_than(self, tmp_path):
        """Verify a size condition cannot be created with a wrongly typed value for greater_than."""
        condition_data = {
            "type": "size",
            "size": 1233,
            "comparison": "lt"
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")

    def test_size_condition_wrongly_typed_inclusive(self, tmp_path):
        """Verify a size condition cannot be created with a wrongly typed value for inclusive."""
        condition_data = {
            "type": "size",
            "size": 1233,
            "comparison": "lt"
        }

        with pytest.raises(ValueError):
            make_condition_from_json(condition_data, "test_rule")