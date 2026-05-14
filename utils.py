import re
import ast

def guess_classname(code: str) -> str:
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name and node.name[0].isupper():
                    return node.name
    except SyntaxError:
        pass
    raise ValueError('Cannot find classname in code. Expected a class definition like `class ClassName:`')


def camel_to_snake(input: str) -> str:
    s1 = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', '_', input)
    return re.sub(r'([0-9])([A-Z])', r'\1_\2', s1).lower()
