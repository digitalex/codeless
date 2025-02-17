import re

_CLASS_FINDER = re.compile(r'^class ([A-Z].*)\(ABC\)')


def guess_classname(code: str) -> str:
    if match := _CLASS_FINDER.search(code):
        return match.group(1)
    raise ValueError('Cannot find classname in code. Expected a class definition like `class ClassName(ABC):`')


def camel_to_snake(input: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', input).lower()
