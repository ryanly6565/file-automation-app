import pytest
import json
from src.config_loader import make_actions_from_json
from src.actions import *

class TestActionConfigLoader:
    def test_missing_actions_type(self):
        """Verify an error is thrown when trying to read a condition missing a type"""
        actions_data = {}

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_wrong_typed_condition_type(self):
        """Verify an error is thrown when trying to read a condition missing a type"""
        actions_data = {
            "type": 12
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestMoveActionConfigLoader:
    def test_move_action_created(self, tmp_path):
        """Verify a move action can successfully be created"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        dst_dir = tmp_path / "destination"
        dst_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("hello")

        actions_data = {
            "type": "move",
            "destination": str(dst_dir)
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        result = actions[0].execute(Path(file))
        assert not file.exists()
        assert (dst_dir / "test.txt").exists()
        assert result.current_path == (dst_dir / "test.txt")

    def test_move_action_missing_dst(self):
        """Verify an error is thrown when trying to read a move action missing a destination"""
        actions_data = {
            "type": "move",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_move_action_wrong_value_dst(self):
        """Verify an error is thrown when trying to read a move action with a wrongly typed destination"""
        actions_data = {
            "type": "move",
            "destination": 4
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestCopyActionConfigLoader:
    def test_copy_action_created(self, tmp_path):
        """Verify a copy action can successfully be created"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        dst_dir = tmp_path / "destination"
        dst_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("hello")

        actions_data = {
            "type": "copy",
            "destination": str(dst_dir)
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        result = actions[0].execute(Path(file))
        assert file.exists()
        assert (dst_dir / "test.txt").exists()
        assert result.current_path == file

    def test_copy_action_missing_dst(self):
        """Verify an error is thrown when trying to read a copy action missing a destination"""
        actions_data = {
            "type": "copy",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_copy_action_wrong_value_dst(self):
        """Verify an error is thrown when trying to read a copy action with a wrongly typed destination"""
        actions_data = {
            "type": "copy",
            "destination": 4
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestPrefixRenameActionConfigLoader:
    def test_prefix_rename_action_created(self, tmp_path):
        """Verify a prefix rename action can successfully be created"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("hello")

        actions_data = {
            "type": "prefix_rename",
            "value": "new_"
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        result = actions[0].execute(Path(file))
        assert not file.exists()
        assert (source_dir / "new_test.txt").exists()
        assert result.current_path == source_dir / "new_test.txt"

    def test_prefix_rename_action_missing_type(self):
        """Verify an error is thrown when trying to read a prefix rename action missing a destination"""
        actions_data = {
            "type": "prefix_rename",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_prefix_rename_action_wrong_value_type(self):
        """Verify an error is thrown when trying to read a prefix rename action with a wrongly typed destination"""
        actions_data = {
            "type": "prefix_rename",
            "value": 4
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestSuffixRenameActionConfigLoader:
    def test_suffix_rename_action_created(self, tmp_path):
        """Verify a suffix rename action can successfully be created"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("hello")

        actions_data = {
            "type": "suffix_rename",
            "value": "_finished"
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        result = actions[0].execute(Path(file))
        assert not file.exists()
        assert (source_dir / "test_finished.txt").exists()
        assert result.current_path == source_dir / "test_finished.txt"

    def test_suffix_rename_action_missing_type(self):
        """Verify an error is thrown when trying to read a suffix rename action missing a destination"""
        actions_data = {
            "type": "suffix_rename",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_suffix_rename_action_wrong_value_type(self):
        """Verify an error is thrown when trying to read a suffix rename action with a wrongly typed destination"""
        actions_data = {
            "type": "suffix_rename",
            "value": 4
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestReplaceTextActionConfigLoader:
    def test_replace_text_action_created(self, tmp_path):
        """Verify a replace text action can successfully be created"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test_test.txt"
        file.write_text("hello")

        actions_data = {
            "type": "replace_text",
            "old_str": "test",
            "new_str": "report",
            "first_instance_only": False,
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        result = actions[0].execute(Path(file))
        assert not file.exists()
        assert (source_dir / "report_report.txt").exists()
        assert result.current_path == source_dir / "report_report.txt"

    def test_replace_text_action_missing_old_str(self):
        """Verify an error is thrown when trying to read a replace text action missing an old_str"""
        actions_data = {
            "type": "replace_text",
            "new_str": "report",
            "first_instance_only": False,
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_replace_text_action_missing_new_str(self):
        """Verify an error is thrown when trying to read a replace text action missing a new_str"""
        actions_data = {
            "type": "replace_text",
            "old_str": "test",
            "first_instance_only": False,
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_replace_text_action_missing_first_instance_only_allowed(self, tmp_path):
        """Verify a replace text action can successfully be created even without a first_instance_only"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test_test.txt"
        file.write_text("hello")

        actions_data = {
            "type": "replace_text",
            "old_str": "test",
            "new_str": "report",
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        result = actions[0].execute(Path(file))
        assert not file.exists()
        assert (source_dir / "report_test.txt").exists()
        assert result.current_path == source_dir / "report_test.txt"

    def test_replace_text_action_wrong_value_old_str(self):
        """Verify an error is thrown when trying to read a replace text action with a wrongly typed old_str"""
        actions_data = {
            "type": "replace_text",
            "old_str": 1,
            "new_str": "report",
            "first_instance_only": False,
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_replace_text_action_wrong_value_new_str(self):
        """Verify an error is thrown when trying to read a replace text action with a wrongly typed new_str"""
        actions_data = {
            "type": "replace_text",
            "old_str": "test",
            "new_str": False,
            "first_instance_only": False,
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_replace_text_action_wrong_value_first_instance_only(self):
        """Verify an error is thrown when trying to read a replace text action with a wrongly typed first_instance_only"""
        actions_data = {
            "type": "replace_text",
            "old_str": "test",
            "new_str":"report",
            "first_instance_only": "this",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_replace_text_action_empty_old_str(self):
        """Verify an error is thrown when trying to read a replace text action with an empty old_str"""
        actions_data = {
            "type": "replace_text",
            "old_str": "",
            "new_str":"report",
            "first_instance_only": True,
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestChangeExtensionActionConfigLoader:
    def test_change_extension_action_created(self, tmp_path):
        """Verify a change extension action can successfully be created"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("test")

        actions_data = {
            "type": "change_extension",
            "new_ext": "md",
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        result = actions[0].execute(Path(file))
        assert not file.exists()
        assert (source_dir / "test.md").exists()
        assert result.current_path == source_dir / "test.md"

    def test_change_extension_action_missing_new_ext(self):
        """Verify an error is thrown when trying to read a change extension action missing a new_ext"""
        actions_data = {
            "type": "change_extension",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_change_extension_action_wrongly_typed_new_ext(self):
        """Verify an error is thrown when trying to read a change extension action with a wrongly typed new_ext"""
        actions_data = {
            "type": "change_extension",
            "new_ext": 2
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_change_extension_action_empty_new_ext(self):
        """Verify an error is thrown when trying to read a change extension action with an empty new_ext"""
        actions_data = {
            "type": "change_extension",
            "new_ext": ""
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_change_extension_action_only_a_dot_new_ext(self):
        """Verify an error is thrown when trying to read a change extension action with a new_ext thats only a ."""
        actions_data = {
            "type": "change_extension",
            "new_ext": "."
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestDeleteActionConfigLoader:
    def test_delete_action_created_trash_bin(self, tmp_path):
        """Verify a delete action can successfully be created that goes to the trash bin"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("test")

        actions_data = {
            "type": "delete",
            "trash_bin": True,
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        assert isinstance(actions[0], DeleteAction)
        assert actions[0].trash_bin is True

    def test_delete_action_created_no_trash_bin(self, tmp_path):
        """Verify a delete action can successfully be created that does not go to the trash bin"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("test")

        actions_data = {
            "type": "delete",
            "trash_bin": False,
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        assert isinstance(actions[0], DeleteAction)
        assert actions[0].trash_bin is False

    def test_delete_action_missing_trash_bin(self):
        """Verify an error is thrown when trying to read a delete action missing a trash_bin"""
        actions_data = {
            "type": "delete",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_delete_action_wrongly_typed_trash_bin(self):
        """Verify an error is thrown when trying to read a delete action with a wrongly typed trash_bin"""
        actions_data = {
            "type": "delete",
            "trash_bin": 2
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

class TestCompressActionConfigLoader:
    def test_compress_action(self, tmp_path):
        actions_data = {
            "type": "compress",
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        assert isinstance(actions[0], CompressAction)

class TestExecuteScriptActionConfigLoader:
    def test_execute_script_action_created(self, tmp_path):
        """Verify an execute script action can successfully be created"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file = source_dir / "test.txt"
        file.write_text("hello")

        script = tmp_path / "test_script.py"
        script.write_text(
"""
from pathlib import Path
import sys

input_path = Path(sys.argv[1])
input_path.with_name("script_ran.txt").write_text("worked")
"""
        )

        actions_data = {
            "type": "execute_script",
            "source": str(script),
            "script_type": "python"
        }

        actions = make_actions_from_json([actions_data], "test_rule")
        new_file = source_dir / "script_ran.txt"

        result =  actions[0].execute(Path(file))
        result_path = result.current_path
        assert file.exists()
        assert file.read_text() == "hello"
        assert new_file.exists()
        assert new_file.read_text() == "worked"
        assert result_path == file

    def test_execute_script_action_missing_source(self, tmp_path):
        """Verify an error is thrown when trying to read an execute script action with a missing source"""
        actions_data = {
            "type": "execute_script",
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_execute_script_action_wrongly_typed_source(self, tmp_path):
        """Verify an error is thrown when trying to read an execute script action with a wrongly typed source"""
        actions_data = {
            "type": "execute_script",
            "source": 4
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_execute_script_action_wrongly_typed_script_type(self, tmp_path):
        """Verify an error is thrown when trying to read an execute script action with a wrongly typed script type"""
        actions_data = {
            "type": "execute_script",
            "source": "dummy_script.py",
            "script_type": 3
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")

    def test_execute_script_action_unknown_script_type(self, tmp_path):
        """Verify an error is thrown when trying to read an execute script action with an unknown script type"""
        actions_data = {
            "type": "execute_script",
            "source": "dummy_script.py",
            "script_type": "unknown_type"
        }

        with pytest.raises(ValueError):
            make_actions_from_json([actions_data], "test_rule")