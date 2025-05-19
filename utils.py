"""
General utility functions for string manipulation and code parsing.
"""
import re

_CLASS_FINDER_REGEX = r'^class ([A-Z].*)\(ABC\)'
_CLASS_FINDER = re.compile(_CLASS_FINDER_REGEX)

# Pattern for converting camelCase to snake_case.
# Handles: standard camel, initialisms (e.g. HTTPRequest), numbers (e.g. Version1)
_SNAKE_CASE_PATTERN = re.compile(
    r'(?<=[a-z])(?=[A-Z])|'       # aZ -> a_Z
    r'(?<=[A-Z])(?=[A-Z][a-z])|'  # AZa -> A_Za
    r'(?<=[a-z])(?=[A-Z]{2,})'    # aZZ -> a_ZZ (handles initialisms before further caps)
)


def guess_classname(code: str) -> str:
    """
    Guesses the class name from a string of Python code.

    Expects a class definition in the format `class ClassName(ABC):`.

    Args:
        code: The Python code string.

    Returns:
        The guessed class name.

    Raises:
        ValueError: If a class name cannot be found in the expected format.
    """
    if match := _CLASS_FINDER.search(code):
        return match.group(1)
    raise ValueError(
        'Cannot find classname in code. Expected a class definition like `class ClassName(ABC):`'
    )


def camel_to_snake(text: str) -> str:
    """
    Converts a camelCase string to snake_case.

    Args:
        text: The camelCase string.

    Returns:
        The snake_case version of the string.
    """
    return _SNAKE_CASE_PATTERN.sub('_', text).lower()
