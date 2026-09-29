from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import subprocess
from src.logger import get_logger
from dataclasses import dataclass
import send2trash
import zipfile

SUPPORTED_SCRIPT_TYPES = {
    "python": (".py",),
    "bash": (".sh", ""),
    "javascript": (".js", ".mjs", ".cjs"),
    "powershell": (".ps1",),
}

@dataclass
class ActionResult:
    # the next path we should operate on
    current_path: Path
    # any other generated paths
    generated_paths: list[Path]
    
class Action(ABC):
    @abstractmethod
    def execute(self, path: Path) -> ActionResult:
        pass

class MoveAction(Action):
    """Action for moving a file to another location."""
    def __init__(self, dst_directory: Path, collision_policy: str ="rename"):
        self.dst_directory = Path(dst_directory)

        valid_policies = {"rename", "overwrite", "skip"}
        if collision_policy not in valid_policies:
            raise ValueError(f"Invalid collision policy: {collision_policy}")
        self.collision_policy = collision_policy

    def __str__(self):
        return "Move the file to " + str(self.dst_directory) + "."

    def execute(self, path: Path) -> ActionResult:
        """Move the given file into the destination directory."""
        destination = self.dst_directory / path.name

        if self.collision_policy == "rename":
            destination = get_available_path(destination)

        elif self.collision_policy == "skip":
            if destination.exists():
                return ActionResult(current_path=path, generated_paths=[])

        shutil.move(path, destination)
        return ActionResult(current_path=destination, generated_paths=[])

class CopyAction(Action):
    """Action for copying a file to another location."""
    def __init__(self, dst_directory: Path, collision_policy: str ="rename"):
        self.dst_directory = Path(dst_directory)

        valid_policies = {"rename", "overwrite", "skip"}
        if collision_policy not in valid_policies:
            raise ValueError(f"Invalid collision policy: {collision_policy}")
        self.collision_policy = collision_policy

    def __str__(self):
        return "Copy the file to " + str(self.dst_directory) + "."

    def execute(self, path: Path) -> ActionResult:
        """Copy the given file into the destination directory."""
        destination = self.dst_directory / path.name

        if self.collision_policy == "rename":
            destination = get_available_path(destination)

        elif self.collision_policy == "skip":
            if destination.exists():
                return ActionResult(current_path=path, generated_paths=[])

        shutil.copy(path, destination)
        return ActionResult(current_path=path, generated_paths=[destination])

class PrefixRenamingAction(Action):
    """Action for adding a prefix to a file."""
    def __init__(self, new_prefix: str):
        if new_prefix == "":
            raise ValueError("Prefix cannot be empty.")
        self.new_prefix = new_prefix

    def __str__(self):
        return f"Add the prefix: \"{self.new_prefix}\"."

    def execute(self, path: Path) -> ActionResult:
        """Rename the given file to have the appropiate prefix."""
        new_name = self.new_prefix + path.name
        new_path = path.with_name(new_name)
        new_path = get_available_path(new_path)

        path.rename(new_path)
        return ActionResult(current_path=new_path, generated_paths=[])

class SuffixRenamingAction(Action):
    """Action for adding a suffix to a file."""
    def __init__(self, new_suffix: str):
        if new_suffix == "":
            raise ValueError("Suffix cannot be empty.")
        self.new_suffix = new_suffix

    def __str__(self):
        return f"Add the suffix: \"{self.new_suffix}\"."

    def execute(self, path: Path) -> ActionResult:
        """Rename the given file to have the appropriate suffix."""
        new_name = path.stem + self.new_suffix + path.suffix
        new_path = path.with_name(new_name)
        new_path = get_available_path(new_path)

        path.rename(new_path)
        return ActionResult(current_path=new_path, generated_paths=[])

class ReplaceTextAction(Action):
    """Action for replacing text in a file name."""
    def __init__(self, old_str: str, new_str: str, first_instance_only: bool=True):
        if old_str == "":
            raise ValueError("Old string cannot be empty.")
        self.old_str = old_str
        self.new_str = new_str
        self.first_instance_only = first_instance_only

    def __str__(self):
        first_instance_only_str = "first instance only" if self.first_instance_only else "every instance"
        return f'Replace the string "{self.old_str}" with the string "{self.new_str}" ({first_instance_only_str}, not including extension).'

    def execute(self, path: Path) -> ActionResult:
        """Rename the given file to have replace the specified text."""
        if (self.old_str not in path.stem):
            return ActionResult(path, generated_paths=[])

        if (self.first_instance_only):
            new_stem = path.stem.replace(self.old_str, self.new_str, 1)
        else:
            new_stem = path.stem.replace(self.old_str, self.new_str)
        new_path = path.with_name(new_stem + path.suffix)

        if new_path != path:
            new_path = get_available_path(new_path)
            path.rename(new_path)

        return ActionResult(current_path=new_path, generated_paths=[])


class ChangeExtensionAction(Action):
    """Action for changing extension in a file name."""
    def __init__(self, new_ext: str):
        if not new_ext or new_ext == ".":
            raise ValueError("New extension cannot be empty or just a period.")
        
        if (not new_ext.startswith(".")):
            self.new_ext = "." + new_ext
        else:
            self.new_ext = new_ext

    def __str__(self):
        return f'Replace the extension of the file with "{self.new_ext}".'

    def execute(self, path: Path) -> ActionResult:
        """Replace the given file extension."""
        new_path = path.with_name(path.stem + self.new_ext)

        if new_path != path:
            new_path = get_available_path(new_path)
            path.rename(new_path)

        return ActionResult(current_path=new_path, generated_paths=[])

class ExecuteScriptAction(Action):
    """Action for executing some external script on this file."""
    def __init__(self, source: Path, script_type: str="python"):
        self.script = Path(source)

        if script_type not in SUPPORTED_SCRIPT_TYPES:
            raise ValueError(f'Script type "{script_type}" is not supported.')
        self.script_type = script_type

        if self.script.suffix not in SUPPORTED_SCRIPT_TYPES[script_type]:
            allowed_ext = ", ".join(
                "no extension" if ext == "" else ext
                for ext in SUPPORTED_SCRIPT_TYPES[script_type]
            )
            raise ValueError(f'Script file "{self.script}" type is not supported. Allowed extensions: {allowed_ext}')

    def __str__(self):
        return f"Run the script: {self.script}, with the file path as the first arg."

    def execute(self, path: Path) -> ActionResult:
        """Execute the script if it is still there."""
        if not self.script.exists() or not self.script.is_file():
            get_logger().error('Script file "%s" is missing or not a script.', self.script )
            raise FileNotFoundError(f'Script file "{self.script}" is missing or is not a file.')

        match self.script_type:
            case "python":
                command = ["python3", str(self.script), str(path)]

            case "bash":
                command = ["bash", str(self.script), str(path)]

            case "javascript":
                command = ["node", str(self.script), str(path)]

            case "powershell":
                command = ["pwsh", str(self.script), str(path)]

            case _:
                raise ValueError(
                    f'Script type "{self.script_type}" is not supported.'
                )

        subprocess.run(command, check=True)
        return ActionResult(current_path=path, generated_paths=[])
    
class DeleteAction(Action):
    """Action for deleting a file."""
    def __init__(self, trash_bin: bool):
        self.trash_bin = trash_bin

    def __str__(self):
        if self.trash_bin:
            return "Move the file to the trash."
        return "Delete the file permanently."

    def execute(self, path: Path) -> ActionResult:
        """Delete the given file."""
        if self.trash_bin:
            send2trash.send2trash(path)
        else:
            path.unlink()

        return ActionResult(path, [])

class CompressAction(Action):
    """Action for compressing a file."""
    def __str__(self):
        return f"Compress the file into a ZIP, further actions happen on the original."

    def execute(self, path: Path) -> ActionResult:
        """Compress the given file."""
        zip_path = path.with_suffix(".zip")
        zip_path = get_available_path(zip_path)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(path, arcname=path.name)

        return ActionResult(current_path=path, generated_paths=[zip_path])


def get_available_path(path: Path) -> Path:
    new_path = path
    counter = 1
    while new_path.exists():
        new_path = path.parent / f"{path.stem} ({counter}){path.suffix}"
        counter += 1
    return new_path
