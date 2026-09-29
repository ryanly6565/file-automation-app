from pathlib import Path

from src.conditions import Condition
from src.actions import Action, ActionResult
from typing import Callable

class Rule:
    """Associates a condition with an action to perform on files mathcing the condition."""
    def __init__(
            self, condition: Condition, 
            actions: list[Action], 
            watch_folder: Path, 
            name: str, 
            enabled: bool=True,
            recursive: bool=False
    ):
        self.name = name
        self.condition = condition
        self.watch_folder = watch_folder
        self.actions = actions
        self.enabled = enabled
        self.recursive = recursive

    def matches(self, path: Path) -> bool:
        """Returns True if the file matches the condition."""
        if not self.enabled:
            return False

        return self.condition.matches(path)

    def execute(self, path: Path, on_action_complete: Callable[[ActionResult], None] | None = None) -> ActionResult:
        """Applies the requested action."""
        curr_path = path
        generated_paths = []

        for action in self.actions:
            result = action.execute(curr_path)
            curr_path = result.current_path
            generated_paths.extend(result.generated_paths)

            if on_action_complete is not None:
                on_action_complete(result)
        return ActionResult(current_path=curr_path, generated_paths=generated_paths)

    