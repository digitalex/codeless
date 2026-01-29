import re

_CLASS_FINDER = re.compile(r'^\s*class\s+([A-Z][a-zA-Z0-9_]*).*:')


def guess_classname(code: str) -> str:
    for line in code.splitlines():
        if match := _CLASS_FINDER.search(line):
            return match.group(1)
    raise ValueError('Cannot find classname in code. Expected a class definition like `class ClassName:`')


def camel_to_snake(input: str) -> str:
    s1 = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', '_', input)
    return re.sub(r'([0-9])([A-Z])', r'\1_\2', s1).lower()
