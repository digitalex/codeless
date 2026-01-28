import re

# Improved regex to handle multiline but still primarily line-based for simplicity.
# We'll stick to a slightly improved version but acknowledge its limitations.
_CLASS_FINDER = re.compile(r'^\s*class\s+([A-Z][a-zA-Z0-9_]*)', re.MULTILINE)


def guess_classname(code: str) -> str:
    # Strip docstrings if possible at the start to avoid false positives
    # but for simplicity we'll just search for the first match that looks like a real class
    # and hope it's not in a comment/docstring.
    # A better way would be using `ast` module.
    import ast
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name[0].isupper():
                    return node.name
    except SyntaxError:
        # Fallback to regex if it's a snippet
        if match := _CLASS_FINDER.search(code):
            return match.group(1)

    raise ValueError('Cannot find classname in code. Expected a class definition like `class ClassName:`')


def camel_to_snake(input: str) -> str:
    # Insert underscore before capital letters if preceded by lowercase or at start (if followed by lowercase)
    # and handles acronyms.
    s1 = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', '_', input)
    # Insert underscore between number and capital letter
    s2 = re.sub(r'([0-9])([A-Z])', r'\1_\2', s1)
    # Insert underscore between letter and number if needed?
    # The previous tests expect Class123Name -> class123_name, so letter-number doesn't need _
    # But what about 123MyClass? s2 handles it.
    return s2.lower()
