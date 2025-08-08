import re

_CLASS_FINDER = re.compile(r'class\s+([A-Z][a-zA-Z0-9_]*)')


def guess_classname(code: str) -> str:
    if match := _CLASS_FINDER.search(code):
        return match.group(1)
    raise ValueError('Cannot find classname in code. Expected a class definition like `class ClassName(ABC):`')


def camel_to_snake(input: str) -> str:
    s1 = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', '_', input)
    s2 = re.sub(r'([a-zA-Z])([0-9])', r'\1_\2', s1)
    return re.sub(r'([0-9])([A-Z])', r'\1_\2', s2).lower()
