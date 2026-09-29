from abc import ABC, abstractmethod
from pathlib import Path

class Condition(ABC):
    @abstractmethod
    def matches(self, path: Path) -> bool:
        pass

class ExtensionCondition(Condition):
    """Condition for checking the file's extension matches some other known file extension."""
    def __init__(self, extension: str):
        self.extension = extension

    def __str__(self):
        return f"Extension is {self.extension}"

    def matches(self, path: Path) -> bool:
        """Returns True if the file extension matches the stored one."""
        return path.suffix == self.extension


class NameContainsCondition(Condition):
    """Condition for checking the file's name contains some substring."""
    def __init__(self, substr: str, case_matters: bool=False):
        self.substr = substr
        self.case_matters = case_matters
        
    def __str__(self):
        if self.case_matters:
            return f"Name contains {self.substr} (respecting case)"
        else:
            return f"Name contains {self.substr} (ignoring case)"

    def matches(self, path: Path) -> bool:
        """Returns True if the file name contains the stored substring."""
        if self.case_matters:
            return self.substr in path.name
        else:
            return self.substr.lower() in path.name.lower()

class AndCondition(Condition):
    """Condition for checking the file's matches multiple conditions simultaneously. If no conditions then False."""
    def __init__(self, conditions: list[Condition]):
        self.conditions = conditions
        
    def __str__(self):
        return "(" + " AND ".join(str(c) for c in self.conditions) + ")"

    def matches(self, path: Path) -> bool:
        """Returns True if the file matches all conditions."""
        if len(self.conditions) == 0:
            return False
        return all([condition.matches(path) for condition in self.conditions])

class OrCondition(Condition):
    """Condition for checking the file's matches at least one of multiple conditions. If no conditions then False."""
    def __init__(self, conditions: list[Condition]):
        self.conditions = conditions

    def __str__(self):
        return "(" + " OR ".join(str(c) for c in self.conditions) + ")"
    
    def matches(self, path: Path) -> bool:
        """Returns True if the file matches at least one conditions."""
        if len(self.conditions) == 0:
            return False
        return any([condition.matches(path) for condition in self.conditions])

class SizeCondition(Condition):
    """Condition for checking the file's size is greater or less than a certain value. By default greater than."""
    def __init__(self, size: int, comparison: str):
        self.size = size
        self.comparison = comparison

    def __str__(self):
        comparison_text = {
            "gt": "strictly greater than",
            "gte": "greater than or equal to",
            "eq": "equal to",
            "lt": "strictly less than",
            "lte": "less than or equal to",
        }
        
        return f"The file size is {comparison_text[self.comparison]} {self.size} bytes"

    def matches(self, path: Path) -> bool:
        file_size = path.stat().st_size

        if self.comparison == "gt":
            return file_size > self.size
        elif self.comparison == "gte":
            return file_size >= self.size
        elif self.comparison == "eq":
            return file_size == self.size
        elif self.comparison == "lt":
            return file_size < self.size
        elif self.comparison == "lte":
            return file_size <= self.size

        raise ValueError(
            f"Unknown size comparison: {self.comparison}"
        )


class NameStartsWithCondition(Condition):
    """Condition for checking the file's name starts with some substring."""
    def __init__(self, substr: str, case_matters: bool=False, include_extension: bool = True):
        self.substr = substr
        self.case_matters = case_matters
        self.include_extension = include_extension
        
    def __str__(self):
        extension_text = "including extension" if self.include_extension else "ignoring extension"
        case_text = "respecting case" if self.case_matters else "ignoring case"
        return f"Name starts with {self.substr} ({extension_text} and {case_text})"

    def matches(self, path: Path) -> bool:
        """Returns True if the file name starts with the stored substring."""
        path_name = path.name if self.include_extension else path.stem
        if self.case_matters:
            return path_name.startswith(self.substr)
        else:
            return path_name.lower().startswith(self.substr.lower())

        
class NameEndsWithCondition(Condition):
    """Condition for checking whether a file name ends with a substring."""
    def __init__(self, substr: str, case_matters: bool = False, include_extension: bool = True):
        self.substr = substr
        self.case_matters = case_matters
        self.include_extension = include_extension

    def __str__(self):
        extension_text = "including extension" if self.include_extension else "ignoring extension"
        case_text = "respecting case" if self.case_matters else "ignoring case"
        return f"Name ends with {self.substr} ({extension_text} and {case_text})"

    def matches(self, path: Path) -> bool:
        """Returns True if the file name ends with the stored substring."""
        path_name = path.name if self.include_extension else path.stem
        if self.case_matters:
            return path_name.endswith(self.substr)
        else:
            return path_name.lower().endswith(self.substr.lower())


class ExactNameCondition(Condition):
    """Condition for checking the file's name matches some string."""
    def __init__(self, match_str: str, case_matters: bool=False, include_extension: bool=True):
        self.match_str = match_str
        self.case_matters = case_matters
        self.include_extension = include_extension
        
    def __str__(self):
        extension_text = "including extension" if self.include_extension else "ignoring extension"
        case_text = "respecting case" if self.case_matters else "ignoring case"
        return f"Name is {self.match_str} ({extension_text} and {case_text})"

    def matches(self, path: Path) -> bool:
        """Returns True if the file matches the stored string."""
        path_name = path.name if self.include_extension else path.stem
        if self.case_matters:
            return path_name == self.match_str
        else:
            return path_name.lower() == self.match_str.lower()