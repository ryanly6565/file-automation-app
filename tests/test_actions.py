from pathlib import Path
from src.actions import *
import pytest
import subprocess
import sys
import pytest

class TestMoveAction:
    def test_move_action_moves_file(self, tmp_path):
        """Verify that moving a file successfully removes from the source and creates in the destination."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")

        action = MoveAction(destination_dir)
        result = action.execute(file)
        result_path = result.current_path

        assert not file.exists()
        assert (destination_dir / "example.txt").exists()
        assert result_path == destination_dir / "example.txt"

    def test_move_action_copies_contents(self, tmp_path):
        """Verify that moving a file successfully copies its contents."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")

        action = MoveAction(destination_dir)
        result = action.execute(file)
        result_path = result.current_path

        assert (destination_dir / "example.txt").read_text() == "hello"
        assert result_path == destination_dir / "example.txt"

    def test_move_action_file_exists(self, tmp_path):
        """Verify that moving a file successfully moves from the source and creates in the destination but renames it."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "example.txt"
        source_dir.mkdir()
        destination_dir.mkdir()

        file = source_dir / "example.txt"
        same_name_file = destination_dir / "example.txt"
        same_name_file.write_text("same_name")
        file.write_text("hello")

        action = MoveAction(destination_dir)
        result = action.execute(file)
        result_path = result.current_path

        assert same_name_file.exists()
        assert same_name_file.read_text() == "same_name"
        assert (destination_dir / "example (1).txt").exists()
        assert (destination_dir / "example (1).txt").read_text() == "hello"
        assert result_path == destination_dir / "example (1).txt"

    def test_move_action_rename_collision(self, tmp_path):
        """Verify that moving a file with rename explicitly declared renames the file properly on collision."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        source = source_dir / "file.txt"
        source.write_text("new")

        existing = destination_dir / "file.txt"
        existing.write_text("old")

        action = MoveAction(destination_dir, collision_policy="rename")
        result = action.execute(source)
        result_path = result.current_path

        assert result_path == destination_dir / "file (1).txt"
        assert result_path.read_text() == "new"
        assert existing.read_text() == "old"


    def test_move_action_overwrite_collision(self, tmp_path):
        """Verify that moving a file with overwrite explicitly declared overwrites the file properly on collision."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        source = source_dir / "file.txt"
        source.write_text("new")

        destination = destination_dir / "file.txt"
        destination.write_text("old")

        action = MoveAction(destination_dir, collision_policy="overwrite")
        result = action.execute(source)
        result_path = result.current_path

        assert result_path == destination
        assert destination.read_text() == "new"
        assert not source.exists()


    def test_move_action_skip_collision(self, tmp_path):
        """Verify that moving a file with skip explicitly declared doesn't do anything on collision."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        source = source_dir / "file.txt"
        source.write_text("new")

        destination = destination_dir / "file.txt"
        destination.write_text("old")

        action = MoveAction(destination_dir, collision_policy="skip")
        result = action.execute(source)
        result_path = result.current_path

        assert result_path == source
        assert source.exists()
        assert source.read_text() == "new"
        assert destination.read_text() == "old"

    def test_move_action_invalid_collision_policy_raises(self, tmp_path):
        """Verify that making a move action with an invalid colliusion policy errors out."""
        with pytest.raises(ValueError):
            MoveAction(tmp_path, collision_policy="invalid")

class TestCopyAction:
    def test_copy_action_copies_file(self, tmp_path):
        """Verify that moving a file successfully stays in the source and creates in the destination."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")

        action = CopyAction(destination_dir)
        result = action.execute(file)
        result_path = result.current_path

        assert file.exists()
        assert (destination_dir / "example.txt").exists()
        assert result_path == source_dir / "example.txt"

    def test_copy_action_copies_contents(self, tmp_path):
        """Verify that moving a file successfully copies its contents."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")

        action = CopyAction(destination_dir)
        result = action.execute(file)
        result_path = result.current_path

        assert (destination_dir / "example.txt").read_text() == "hello"
        assert result_path == source_dir / "example.txt"

    def test_copy_action_file_exists(self, tmp_path):
        """Verify that moving a file successfully stays in the source and creates in the destination but is renamed."""
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"

        source_dir.mkdir()
        destination_dir.mkdir()

        file = source_dir / "example.txt"
        same_name_file = destination_dir / "example.txt"
        same_name_file.write_text("same_name")
        file.write_text("hello")

        action = CopyAction(destination_dir)
        result = action.execute(file)
        result_path = result.current_path

        assert file.exists()
        assert same_name_file.exists()
        assert same_name_file.read_text() == "same_name"
        assert (destination_dir / "example (1).txt").exists()
        assert (destination_dir / "example (1).txt").read_text() == "hello"
        assert result_path == source_dir / "example.txt"
        assert result_path == source_dir / "example.txt"

    def test_copy_action_rename_collision(self, tmp_path):
        """Verify that copying a file with rename explicitly declared renames the file properly on collision."""
        source = tmp_path / "file.txt"
        destination_dir = tmp_path / "destination"

        destination_dir.mkdir()

        source.write_text("new")

        existing = destination_dir / "file.txt"
        existing.write_text("old")

        action = CopyAction(destination_dir, collision_policy="rename")
        action.execute(source)

        renamed = destination_dir / "file (1).txt"

        assert renamed.exists()
        assert renamed.read_text() == "new"
        assert existing.read_text() == "old"
        assert source.exists()


    def test_copy_action_overwrite_collision(self, tmp_path):
        """Verify that copying a file with rename explicitly declared overwrites the file properly on collision."""
        source = tmp_path / "file.txt"
        destination_dir = tmp_path / "destination"

        destination_dir.mkdir()

        source.write_text("new")

        destination = destination_dir / "file.txt"
        destination.write_text("old")

        action = CopyAction(destination_dir, collision_policy="overwrite")
        action.execute(source)

        assert destination.read_text() == "new"
        assert source.exists()


    def test_copy_action_skip_collision(self, tmp_path):
        """Verify that copying a file with rename explicitly declared does nothing on collision."""
        source = tmp_path / "file.txt"
        destination_dir = tmp_path / "destination"

        destination_dir.mkdir()

        source.write_text("new")

        destination = destination_dir / "file.txt"
        destination.write_text("old")

        action = CopyAction(destination_dir, collision_policy="skip")
        action.execute(source)

        assert destination.read_text() == "old"
        assert source.exists()

    def test_copy_action_invalid_collision_policy_raises(self, tmp_path):
        """Verify that making a copy action with an invalid colliusion policy errors out."""
        with pytest.raises(ValueError):
            CopyAction(tmp_path, collision_policy="invalid")

class TestPrefixRenamingAction:
    def test_prefix_renaming(self, tmp_path):
        """Verify that prefix renaming successfully renames a file."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")

        action = PrefixRenamingAction("new_")
        result = action.execute(file)
        result_path = result.current_path
        new_file = source_dir / "new_example.txt"

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == source_dir / "new_example.txt"

    def test_prefix_renaming_file_exists(self, tmp_path):
        """Verify that prefix renaming successfully renames a file when the new name exists."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")
        old_file = source_dir / "new_example.txt"
        old_file.write_text("old_hello")

        action = PrefixRenamingAction("new_")
        result = action.execute(file)
        result_path = result.current_path
        new_file = source_dir / "new_example (1).txt"

        assert not file.exists()
        assert old_file.exists()
        assert new_file.exists()
        assert old_file.read_text() == "old_hello"
        assert new_file.read_text() == "hello"
        assert result_path == source_dir / "new_example (1).txt"

class TestSuffixRenamingAction:
    def test_suffix_renaming(self, tmp_path):
        """Verify that suffix renaming successfully renames a file when the new name exists."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")

        action = SuffixRenamingAction("_finished")
        result = action.execute(file)
        result_path = result.current_path
        new_file = source_dir / "example_finished.txt"

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == source_dir / "example_finished.txt"

    def test_suffix_renaming_file_exists(self, tmp_path):
        """Verify that suffix renaming successfully renames a file when the new name exists."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")
        old_file = source_dir / "example_finished.txt"
        old_file.write_text("old_hello")

        action = SuffixRenamingAction("_finished")
        result = action.execute(file)
        result_path = result.current_path
        new_file = source_dir / "example_finished (1).txt"

        assert not file.exists()
        assert old_file.exists()
        assert new_file.exists()
        assert old_file.read_text() == "old_hello"
        assert new_file.read_text() == "hello"
        assert result_path == source_dir / "example_finished (1).txt"

    def test_suffix_renaming_file_exists_twice(self, tmp_path):
        """Verify that suffix renaming successfully renames a file when the new name exists (as well as the first choice for alternative name)."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        file = source_dir / "example.txt"
        file.write_text("hello")
        old_file = source_dir / "example_finished.txt"
        old_file.write_text("old_hello")
        old_file_2 = source_dir / "example_finished (1).txt"
        old_file_2.write_text("old_hello_1")

        action = SuffixRenamingAction("_finished")
        result = action.execute(file)
        result_path = result.current_path
        new_file = source_dir / "example_finished (2).txt"

        assert not file.exists()
        assert old_file.exists()
        assert old_file_2.exists()
        assert new_file.exists()
        assert old_file.read_text() == "old_hello"
        assert old_file_2.read_text() == "old_hello_1"
        assert new_file.read_text() == "hello"
        assert result_path == source_dir / "example_finished (2).txt"

class TestExecuteAction:
    def test_execute_script_action_runs_python_script(self, tmp_path):
        """Verify that execute script successfully executes a python."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.py"
        script.write_text(
"""
from pathlib import Path
import sys

input_path = Path(sys.argv[1])
input_path.with_name("script_ran.txt").write_text("worked")
"""
        )

        action = ExecuteScriptAction(script)
        result = action.execute(input_file)
        result_path = result.current_path

        assert result_path == input_file
        assert (tmp_path / "script_ran.txt").exists()
        assert (tmp_path / "script_ran.txt").read_text() == "worked"

    def test_execute_script_action_missing_python_script(self, tmp_path):
        """Verify that execute script errors if no script."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.py"
        action = ExecuteScriptAction(script)

        with pytest.raises(FileNotFoundError):
            action.execute(input_file)

    def test_execute_script_action_wrong_python_extension(self, tmp_path):
        """Verify that execute script errors if the python file has no .py extension."""
        script = tmp_path / "test_script"
        with pytest.raises(ValueError):
            ExecuteScriptAction(script)

    def test_execute_script_python_script_has_error(self, tmp_path):
        """Verify the execute script action propagates an error when the Python script fails."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.py"
        script.write_text(
"""
aaaaaa
"""
        )

        action = ExecuteScriptAction(script)
        with pytest.raises(subprocess.CalledProcessError):
            action.execute(input_file)

    def test_execute_script_python_script_is_directory(self, tmp_path):
        """Verify the execute script action errors if the script is actually a directory."""
        input_dir = tmp_path / "input.txt"
        input_dir.mkdir()

        with pytest.raises(ValueError):
            ExecuteScriptAction(input_dir)

    def test_execute_script_python_script_type_not_supported(self, tmp_path):
            """Verify the execute script action errors if the script type is not supported."""
            script = tmp_path / "test_script.py"
            script.write_text(
"""
from pathlib import Path
import sys

input_path = Path(sys.argv[1])
input_path.with_name("script_ran.txt").write_text("worked")
"""
            )
    
            with pytest.raises(ValueError):
                ExecuteScriptAction(script, script_type="unknown")

    @pytest.mark.skipif(sys.platform == "win32", reason="Bash execution test requires a POSIX-style Bash environment")
    def test_execute_script_action_runs_bash_script(self, tmp_path):
        """Verify that execute script successfully executes a Bash script."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.sh"
        script.write_text(
"""#!/usr/bin/env bash

input_path="$1"
dir="$(dirname "$input_path")"
echo -n "worked" > "$dir/script_ran.txt"
"""
        )

        action = ExecuteScriptAction(script, script_type="bash")
        result = action.execute(input_file)

        assert result.current_path == input_file
        assert result.generated_paths == []
        assert (tmp_path / "script_ran.txt").exists()
        assert (tmp_path / "script_ran.txt").read_text() == "worked"

    @pytest.mark.skipif(sys.platform == "win32", reason="Bash execution test requires a POSIX-style Bash environment")
    def test_execute_script_action_runs_extensionless_bash_script(self, tmp_path):
        """Verify that execute script successfully executes a Bash script with no extension."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script"
        script.write_text(
"""#!/usr/bin/env bash

input_path="$1"
dir="$(dirname "$input_path")"
echo -n "worked" > "$dir/script_ran.txt"
"""
        )

        action = ExecuteScriptAction(script, script_type="bash")
        result = action.execute(input_file)

        assert result.current_path == input_file
        assert result.generated_paths == []
        assert (tmp_path / "script_ran.txt").exists()
        assert (tmp_path / "script_ran.txt").read_text() == "worked"

    @pytest.mark.skipif(sys.platform == "win32", reason="Bash execution test requires a POSIX-style Bash environment")
    def test_execute_script_action_missing_bash_script(self, tmp_path):
        """Verify that execute script errors if the Bash script is missing."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.sh"
        action = ExecuteScriptAction(script, script_type="bash")

        with pytest.raises(FileNotFoundError):
            action.execute(input_file)

    @pytest.mark.skipif(sys.platform == "win32", reason="Bash execution test requires a POSIX-style Bash environment")
    def test_execute_script_action_wrong_bash_extension(self, tmp_path):
        """Verify that Bash rejects an unsupported script extension."""
        script = tmp_path / "test_script.py"

        with pytest.raises(ValueError):
            ExecuteScriptAction(script, script_type="bash")

    @pytest.mark.skipif(sys.platform == "win32", reason="Bash execution test requires a POSIX-style Bash environment")
    def test_execute_script_bash_script_has_error(self, tmp_path):
        """Verify that execute script propagates an error when the Bash script fails."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.sh"
        script.write_text(
"""#!/usr/bin/env bash

exit 1
"""
        )

        action = ExecuteScriptAction(script, script_type="bash")

        with pytest.raises(subprocess.CalledProcessError):
            action.execute(input_file)

    def test_execute_script_bash_script_is_directory(self, tmp_path):
        """Verify that execute script errors if the Bash script path is actually a directory."""
        script = tmp_path / "test_script.sh"
        script.mkdir()

        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        action = ExecuteScriptAction(script, script_type="bash")

        with pytest.raises(FileNotFoundError):
            action.execute(input_file)

    def test_execute_script_action_runs_javascript_script(self, tmp_path):
        """Verify that execute script successfully executes a JavaScript script."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.js"
        script.write_text(
"""const fs = require("fs");
const path = require("path");

const inputPath = process.argv[2];
const dir = path.dirname(inputPath);

fs.writeFileSync(path.join(dir, "script_ran.txt"), "worked");
"""
        )

        action = ExecuteScriptAction(script, script_type="javascript")
        result = action.execute(input_file)

        assert result.current_path == input_file
        assert result.generated_paths == []
        assert (tmp_path / "script_ran.txt").exists()
        assert (tmp_path / "script_ran.txt").read_text() == "worked"

    def test_execute_script_action_accepts_mjs(self, tmp_path):
        """Verify that JavaScript accepts the .mjs extension."""
        script = tmp_path / "test_script.mjs"
        script.write_text("")

        action = ExecuteScriptAction(script, script_type="javascript")

        assert action.script == script
        assert action.script_type == "javascript"

    def test_execute_script_action_accepts_cjs(self, tmp_path):
        """Verify that JavaScript accepts the .cjs extension."""
        script = tmp_path / "test_script.cjs"
        script.write_text("")

        action = ExecuteScriptAction(script, script_type="javascript")

        assert action.script == script
        assert action.script_type == "javascript"

    def test_execute_script_action_missing_javascript_script(self, tmp_path):
        """Verify that execute script errors if the JavaScript script is missing."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.js"
        action = ExecuteScriptAction(script, script_type="javascript")

        with pytest.raises(FileNotFoundError):
            action.execute(input_file)

    def test_execute_script_action_wrong_javascript_extension(self, tmp_path):
        """Verify that JavaScript rejects an unsupported script extension."""
        script = tmp_path / "test_script.py"

        with pytest.raises(ValueError):
            ExecuteScriptAction(script, script_type="javascript")

    def test_execute_script_javascript_script_has_error(self, tmp_path):
        """Verify that execute script propagates an error when the JavaScript script fails."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.js"
        script.write_text(
"""throw new Error("failed");
"""
        )

        action = ExecuteScriptAction(script, script_type="javascript")
        with pytest.raises(subprocess.CalledProcessError):
            action.execute(input_file)


    def test_execute_script_javascript_script_is_directory(self, tmp_path):
        """Verify that execute script errors if the JavaScript script path is actually a directory."""
        script = tmp_path / "test_script.js"
        script.mkdir()

        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        action = ExecuteScriptAction(script, script_type="javascript")
        with pytest.raises(FileNotFoundError):
            action.execute(input_file)

    def test_execute_script_action_accepts_powershell_script(self, tmp_path):
        """Verify that PowerShell accepts the .ps1 extension."""
        script = tmp_path / "test_script.ps1"
        script.write_text("")

        action = ExecuteScriptAction(script, script_type="powershell")

        assert action.script == script
        assert action.script_type == "powershell"

    def test_execute_script_action_missing_powershell_script(self, tmp_path):
        """Verify that execute script errors if the PowerShell script is missing."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.ps1"
        action = ExecuteScriptAction(script, script_type="powershell")

        with pytest.raises(FileNotFoundError):
            action.execute(input_file)

    def test_execute_script_action_wrong_powershell_extension(self, tmp_path):
        """Verify that PowerShell rejects an unsupported script extension."""
        script = tmp_path / "test_script.py"

        with pytest.raises(ValueError):
            ExecuteScriptAction(script, script_type="powershell")

    def test_execute_script_powershell_script_is_directory(self, tmp_path):
        """Verify that execute script errors if the PowerShell script path is a directory."""
        script = tmp_path / "test_script.ps1"
        script.mkdir()

        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        action = ExecuteScriptAction(script, script_type="powershell")
        with pytest.raises(FileNotFoundError):
            action.execute(input_file)

    def test_execute_script_action_runs_powershell_command(self, tmp_path, monkeypatch):
        """Verify that PowerShell execution builds the correct pwsh command."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        script = tmp_path / "test_script.ps1"
        script.write_text('Write-Output "worked"')

        called = {}

        def fake_run(command, check):
            called["command"] = command
            called["check"] = check

        monkeypatch.setattr("src.actions.subprocess.run", fake_run)
        action = ExecuteScriptAction(script, script_type="powershell")
        result = action.execute(input_file)
        assert called["command"] == ["pwsh", str(script), str(input_file),] or \
               called["command"] == ["powershell.exe", str(script), str(input_file),]
        assert called["check"] is True
        assert result.current_path == input_file
        assert result.generated_paths == []

class TestReplaceTextAction:
    def test_replace_text(self, tmp_path):
        """Verify that replace text actually replaces the text."""
        file = tmp_path / "draft_report.txt"
        file.write_text("hello")

        action = ReplaceTextAction("draft", "final")
        result = action.execute(file)
        result_path = result.current_path
        new_file = tmp_path / "final_report.txt"

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == new_file
        assert result.generated_paths == []

    def test_replace_text_first_instance(self, tmp_path):
        """Verify that replace text actually replaces only the first instance of the text when set to do so."""
        file = tmp_path / "draft_report_draft_draft.txt"
        file.write_text("hello")

        action = ReplaceTextAction("draft", "final", True)
        result = action.execute(file)
        result_path = result.current_path
        new_file = tmp_path / "final_report_draft_draft.txt"

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == new_file

    def test_replace_text_every_instance(self, tmp_path):
        """Verify that replace text actually replaces every instance of the text when set to do so."""
        file = tmp_path / "draft_report_draft_draft.txt"
        file.write_text("hello")

        action = ReplaceTextAction("draft", "final", False)
        result = action.execute(file)
        result_path = result.current_path
        new_file = tmp_path / "final_report_final_final.txt"

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == new_file

    def test_replace_text_absent_string(self, tmp_path):
        """Verify that replace text does nothing if the searched string is missing."""
        file = tmp_path / "draft_report.txt"
        file.write_text("hello")

        action = ReplaceTextAction("missing", "final", False)
        result = action.execute(file)
        result_path = result.current_path

        assert file.exists()
        assert file == result_path

    def test_replace_text_collision(self, tmp_path):
        """Verify that replace text successfully renames on collision."""
        file = tmp_path / "draft_report.txt"
        file.write_text("hello")
        old_file = tmp_path / "final_report.txt"
        old_file.write_text("original")
        new_file = tmp_path / "final_report (1).txt"

        action = ReplaceTextAction("draft", "final", False)
        result = action.execute(file)
        result_path = result.current_path

        assert not file.exists()
        assert old_file.exists()
        assert old_file.read_text() == "original"
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == new_file

    def test_replace_text_errors_on_empty_old_string(self, tmp_path):
        """Verify that replace text errors if given an empty old string."""
        with pytest.raises(ValueError):
            ReplaceTextAction("", "new")

    def test_replace_text_does_not_touch_extension(self, tmp_path):
        """Verify that replace text does not touch extension."""
        file = tmp_path / "draft_report.draft"
        file.write_text("hello")
        new_file = tmp_path / "final_report.draft"

        action = ReplaceTextAction("draft", "final", False)
        result = action.execute(file)
        result_path = result.current_path

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == new_file
    
class TestChangeExtensionAction:
    def test_change_extension(self, tmp_path):
        """Verify that change extension actually changes extension."""
        file = tmp_path / "test.txt"
        file.write_text("test")

        action = ChangeExtensionAction(".md")
        result = action.execute(file)
        result_path = result.current_path
        new_file = tmp_path / "test.md"

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "test"
        assert result_path == new_file
        assert result.generated_paths == []

    def test_change_extension_missing_dot(self, tmp_path):
        """Verify that change extension actually changes extension even if the provided extension is missing the period."""
        file = tmp_path / "test.txt"
        file.write_text("test")

        action = ChangeExtensionAction("md")
        result = action.execute(file)
        result_path = result.current_path
        new_file = tmp_path / "test.md"

        assert not file.exists()
        assert new_file.exists()
        assert new_file.read_text() == "test"
        assert result_path == new_file
        assert result.generated_paths == []

    def test_change_extension_same_extension_does_nothing(self, tmp_path):
        """Verify that change extension does nothing to files with same extension."""
        file = tmp_path / "test.txt"
        file.write_text("test")

        action = ChangeExtensionAction(".txt")
        result = action.execute(file)
        result_path = result.current_path

        assert file.exists()
        assert file.read_text() == "test"
        assert result_path == file

    def test_change_extension_collision(self, tmp_path):
        """Verify that change extension successfully renames on collision."""
        file = tmp_path / "test.txt"
        file.write_text("hello")
        old_file = tmp_path / "test.md"
        old_file.write_text("original")
        new_file = tmp_path / "test (1).md"

        action = ChangeExtensionAction(".md")
        result = action.execute(file)
        result_path = result.current_path

        assert not file.exists()
        assert old_file.exists()
        assert old_file.read_text() == "original"
        assert new_file.exists()
        assert new_file.read_text() == "hello"
        assert result_path == new_file

    def test_change_extension_errors_on_empty_extension(self, tmp_path):
        """Verify that change extension errors if given an empty extension."""
        with pytest.raises(ValueError):
            ChangeExtensionAction("")

    def test_change_extension_errors_on_single_dot(self, tmp_path):
        """Verify that change extension errors if given an single period as an extension."""
        with pytest.raises(ValueError):
            ChangeExtensionAction(".")

class TestDeleteAction:
    def test_delete_action_permanent_delete(self, tmp_path):
        """Verify that delete permanently removes the file when set to do so."""
        file = tmp_path / "test.txt"
        file.write_text("hello")

        action = DeleteAction(False)
        result = action.execute(file)

        assert not file.exists()
        assert result.current_path == file
        assert result.generated_paths == []

    def test_delete_action_uses_trash(self, tmp_path, monkeypatch):
        """Verify that trash mode uses send2trash."""
        file = tmp_path / "test.txt"
        file.write_text("hello")

        called = {}

        def fake_send2trash(path):
            called["path"] = path

        # replace send2trash with method, we are only testing to see its valled
        monkeypatch.setattr("src.actions.send2trash.send2trash", fake_send2trash)

        action = DeleteAction(True)
        result = action.execute(file)

        assert called["path"] == file
        assert result.current_path == file
        assert result.generated_paths == []

    def test_delete_action_errors_on_missing_file(self, tmp_path):
        """Verify that deleting a missing file raises an error."""
        file = tmp_path / "missing.txt"
        action = DeleteAction(False)

        with pytest.raises(FileNotFoundError):
            action.execute(file)

class TestCompressAction:
    def test_compress(self, tmp_path):
        """Verify that compress creates the zip file and leaves original unchanged."""
        file = tmp_path / "test.txt"
        file.write_text("hello")
        new_file = tmp_path / "test.zip"

        action = CompressAction()
        result = action.execute(file)

        assert file.exists()
        assert new_file.exists()
        assert file.read_text() == "hello"
        assert result.current_path == file
        assert result.generated_paths == [new_file]

    def test_compress_has_correct_contents(self, tmp_path):
        """Verify that compress creates a zip file that actually has correct contents."""
        tmp_folder = tmp_path / "dir"
        tmp_folder.mkdir()

        file = tmp_path / "test.txt"
        file.write_text("hello")
        zip_file = tmp_path / "test.zip"

        action = CompressAction()
        result = action.execute(file)

        assert file.exists()
        assert zip_file.exists()

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmp_folder)
        extracted_file = tmp_folder / "test.txt"
        assert extracted_file.exists()
        assert file.read_text() == extracted_file.read_text()

    def test_compress_renames_on_first_collision_correctly(self, tmp_path):
        """Verify that compress creates a zip file that is appropiately renamed if the first choice name is taken."""
        tmp_folder = tmp_path / "dir"
        tmp_folder.mkdir()

        file = tmp_path / "test.txt"
        file.write_text("hello")
        old_file = tmp_path / "test.zip"
        old_file.write_text("old")
        zip_file = tmp_path / "test (1).zip"

        action = CompressAction()
        result = action.execute(file)

        assert file.exists()
        assert old_file.exists()
        assert zip_file.exists()
        assert file.read_text() == "hello"
        assert old_file.read_text() == "old"

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmp_folder)
        extracted_file = tmp_folder / "test.txt"
        assert extracted_file.exists()
        assert file.read_text() == extracted_file.read_text()

    def test_compress_renames_on_second_collision_correctly(self, tmp_path):
        """Verify that compress creates a zip file that is apporopaitely renamed if the second choice name is taken."""
        tmp_folder = tmp_path / "dir"
        tmp_folder.mkdir()

        file = tmp_path / "test.txt"
        file.write_text("hello")
        old_file_1 = tmp_path / "test.zip"
        old_file_1.write_text("old1")
        old_file_2 = tmp_path / "test (1).zip"
        old_file_2.write_text("old2")
        zip_file = tmp_path / "test (2).zip"

        action = CompressAction()
        result = action.execute(file)

        assert file.exists()
        assert old_file_1.exists()
        assert old_file_2.exists()
        assert zip_file.exists()
        assert file.read_text() == "hello"
        assert old_file_1.read_text() == "old1"
        assert old_file_2.read_text() == "old2"

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmp_folder)
        extracted_file = tmp_folder / "test.txt"
        assert extracted_file.exists()
        assert file.read_text() == extracted_file.read_text()

